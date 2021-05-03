import time
from typing import Optional

from flask import Flask, request, jsonify, send_from_directory

import misc
from analysis.interface import Predictor
from backend.mail_helpers import Mailer
from data.collector.sources import get_exported_sources, is_valid_source
from data.database import Database, recreate_database, MatchSelector, row_to_post, RangeSelector, FollowedCoin, \
    FollowedSource, SourceSelector
from backend.user import get_user_by_username, verify_password, create_user, UserInfo, \
    check_session, new_session, remove_session
from backend.json_helpers import *
import numpy as np
from flask_cors import CORS

NPM_OUT = "web/web-app/out"

app = Flask(__name__, static_folder=NPM_OUT, static_url_path="/static")
app.secret_key = b'f&#Uj**pF(G6R5O'
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
mailer = Mailer(app)
CORS(app)


@app.route("/send_mail")
def sendmail():
    mailer.send_mail()


def get_coin_type_arg() -> Optional[misc.CoinType]:
    coin_type = request.args.get("type", type=str, default=None)
    if coin_type is None:
        return None
    try:
        # Convert to enum.
        coin_type = misc.CoinType(coin_type)
    except ValueError:
        return None
    return coin_type


def get_token_arg() -> str:
    token = request.args.get("token", type=str, default=None)
    return token


def get_user_from_token(db: Database) -> Optional[UserInfo]:
    token = get_token_arg()
    return check_session(db, token)


# TODO: MAKE PREDICTIONS WHEN THE POST IS COLLECTED AND SAVE IT TO DATABASE. IDEALLY THIS SHOULDN'T BE HERE.
predictor = Predictor("test_model", "Jun19_Feb21_Big")


# SERVE THE FRONTEND
@app.route("/app")
@app.route("/app/")
@app.route("/app/<page>")
def web_app(page: str = "index"):
    # LOL!
    page += ".html"
    return send_from_directory(NPM_OUT, page)


@app.route("/api/posts")
def get_posts():
    start = request.args.get("start", type=int, default=0)
    end = request.args.get("end", type=int, default=int(time.time()))  # Connect to the database
    coin_type = get_coin_type_arg()
    selectors = [RangeSelector("time", start, end)]
    source = request.args.get("source", type=str, default=None)
    order_by = request.args.get("sort", type=str, default=None)
    desc = request.args.get("desc", type=int, default=0)
    limit = request.args.get("limit", type=int, default=50)
    # We return 50 posts per request at most.
    limit = min(limit, 50)
    if coin_type is not None:
        selectors.append(MatchSelector("coin_type", coin_type.value))
    if source is not None and "@" in source:
        sources = source.split(";")
        selectors.append(SourceSelector(sources))
    # Disallow invalid sorting options to prevent SQL injections.
    if order_by is not None and order_by not in ["interaction", "impact", "time", "user"]:
        order_by = None
    # Handle the parameters for infinite scrolling.
    from_interaction = request.args.get("from_interaction", type=int, default=None)
    from_time = request.args.get("from_time", type=int, default=None)
    from_user = request.args.get("from_user", type=str, default=None)
    if from_interaction is not None:
        selectors.append(RangeSelector("interaction",
                                       from_interaction if desc == 0 else None,
                                       from_interaction if desc == 1 else None,
                                       closed=False))
    if from_time is not None:
        selectors.append(RangeSelector("time",
                                       from_time if desc == 0 else None,
                                       from_time if desc == 1 else None,
                                       closed=False))
    if from_user is not None:
        selectors.append(RangeSelector("user",
                                       from_user if desc == 0 else None,
                                       from_user if desc == 1 else None,
                                       closed=False))
    # Connect to the database
    db = Database()
    posts = db.read_by("posts", selectors, row_to_post, order_by=order_by, desc=desc, limit=limit)

    # TODO: MAKE PREDICTIONS WHEN THE POST IS COLLECTED AND SAVE IT TO DATABASE. IDEALLY THIS SHOULDN'T BE HERE.
    if len(posts) > 0:
        posts = predictor.predict(posts)
    # Sort by time.
    return jsonify([post_to_dict(p) for p in posts])


@app.route("/api/user_list")
def get_user_list():
    db = Database()
    return jsonify([])


@app.route("/api/prices")
def get_prices():
    start = request.args.get("start", type=int, default=0)
    end = request.args.get("end", type=int, default=int(time.time()))
    coin_type = get_coin_type_arg()
    if coin_type is None:
        return jsonify({"result": "error", "error_msg": "Invalid coin type."})
    # Connect to the database
    db = Database()
    prices = db.read_prices_by_time_and_coin_type(start, end, coin_type)
    # Sort by time.
    prices = sorted(prices, key=lambda p: p.time, reverse=True)
    return jsonify([price_to_dict(p) for p in prices])


@app.route("/api/coin_list")
def get_coin_list():
    coin_types = []
    for coin_type in misc.CoinType:
        coin_types.append({"name": coin_type,
                           "image": "https://www.dhresource.com/0x0/f2/albu/g9/M00/27/85/rBVaVVxO822ACwv4AALYau1h4a8355.jpg/500pcs-30mm-diameter-bitcoin-logo-label-sticker.jpg"})
    return jsonify(coin_types)


@app.route("/api/source_list")
def get_source_list():
    db = Database()
    users = db.read_users()
    users += [{
        "user": src.user,
        "source": src.source
    } for src in get_exported_sources()]
    uniquesMap = {s["user"] + '@' + s["source"]: s for s in users}
    return jsonify(list(uniquesMap.values()))


@app.route("/api/post_volume")
def calculate_post_volume():
    start = request.args.get("start", type=float, default=0)
    end = request.args.get("end", type=float, default=int(time.time()))
    ticks = request.args.get("ticks", type=int, default=100)
    coin_type = get_coin_type_arg()
    if coin_type is None:
        return jsonify({"result": "error", "error_msg": "Invalid coin type."})
    # Connect to the database
    db = Database()
    posts = db.read_posts_by_time_and_coin_type(start, end, coin_type)
    full_range = end - start
    tick_range = full_range / ticks
    volumes = []
    for (i, curr_tick) in enumerate(np.arange(start, end - tick_range + 1, tick_range)):
        tick_start = curr_tick
        tick_end = curr_tick + tick_range
        count = sum(1 for p in posts if tick_start <= p.time <= tick_end)
        volume = count
        if i > 0:
            volume += volumes[i - 1]['volume']
        volumes.append({
            'time': tick_start,
            'next_time': tick_end,
            'volume': volume,
            'count': count
        })
    return jsonify(volumes)


@app.route("/api/coin_stats")
def get_coin_stats():
    coin_type = get_coin_type_arg()
    top_user_limit = request.args.get("userlimit", type=int, default=5)
    top_source_limit = request.args.get("sourcelimit", type=int, default=5)
    if coin_type is None:
        return jsonify({"result": "error", "error_msg": "Invalid coin type."})
    db = Database()
    top_sources = db.read_top_sources(coin_type, top_source_limit,
                                      lambda row: {"total_msg": row[0],
                                                   "source": "*@" + row[5]})
    top_active_users = db.read_top_active_users(coin_type, top_user_limit,
                                                lambda row: {"total_msg": row[0],
                                                             "source": row[3] + "@" + row[5]})
    top_interacted_users = db.read_top_interacted_users(coin_type, top_user_limit,
                                                        lambda row: {"total_interaction": row[0],
                                                                     "source": row[3] + "@" + row[5]})
    last_price = db.read_last_price(coin_type)
    num_followers = db.read_num_coin_followers(coin_type)
    return jsonify({
        "num_followers": num_followers,
        "top_sources": top_sources,
        "top_active_users": top_active_users,
        "top_interacted_users": top_interacted_users,
        "last_price": dictify(last_price, excluded_keys={"type"})
    })


@app.route("/api/source_stats")
def get_source_stats():
    source = request.args.get("source", type=str, default=None)
    top_user_limit = request.args.get("userlimit", type=int, default=5)
    relevant_coin_limit = request.args.get("coinlimit", type=int, default=5)
    if source is None:
        return jsonify({"result": "error", "error_msg": "Invalid source."})
    db = Database()
    source_parts = source.split("@")
    # Handle the user stat case.
    if source_parts[0] != '*':
        num_followers = db.read_num_user_followers(source_parts[0], source_parts[1])
        return jsonify({
            "num_followers": num_followers
        })
    # Handle the source stat case.
    # Get the top active users.
    top_active_users = db.read_grouped_tops("posts", "user", "COUNT(id)", top_user_limit,
                                            [MatchSelector("source", source_parts[1])],
                                            lambda row: {"total_msg": row[0],
                                                         "source": row[3] + "@" + source_parts[1]})
    # Get the top interacted users.
    top_interacted_users = db.read_grouped_tops("posts", "user", "SUM(interaction)", top_user_limit,
                                                [MatchSelector("source", source_parts[1])],
                                                lambda row: {"total_interaction": row[0],
                                                             "source": row[3] + "@" + source_parts[1]})
    # Get the most relevant coins.
    relevant_coins = db.read_grouped_tops("posts", "coin_type", "COUNT(id)", relevant_coin_limit,
                                          [MatchSelector("source", source_parts[1])],
                                          lambda row: {"msg_count": row[0], "coin_type": row[2]})
    # Get the number of followers.
    num_followers = db.read_num_source_followers(source_parts[1])
    return jsonify({
        "num_followers": num_followers,
        "top_active_users": top_active_users,
        "top_interacted_users": top_interacted_users,
        "relevant_coins": relevant_coins
    })


@app.route("/user/login", methods=["POST"])
def login():
    username = request.form.get("username", default="")
    password = request.form.get("password", default="")
    if username == "" or password == "":
        return jsonify({"result": "error", "error_type": 0, "error_msg": "Please provide credentials."})
    db = Database()
    user = get_user_by_username(db, username)
    # Check the existence of the user.
    if user is None:
        return jsonify({"result": "error", "error_type": 1, "error_msg": "Invalid user."})
    # Check the password.
    if not verify_password(password, user.user.password, user.user.salt):
        return jsonify({"result": "error", "error_type": 2, "error_msg": "Invalid password."})
    token = new_session(db, user.user.id)
    return jsonify({"result": "ok", "token": token})


@app.route("/user/register", methods=["POST"])
def register():
    username = request.form.get("username", default="")
    password = request.form.get("password", default="")
    if username == "" or password == "":
        return jsonify({"result": "error", "error_type": 0, "error_msg": "Please provide credentials."})
    db = Database()
    success = create_user(db, username, password)
    if not success:
        return jsonify({"result": "error", "error_type": 1, "error_msg": "User already exists."})
    return jsonify({"result": "ok"})


@app.route("/user/logout")
def logout():
    token = get_token_arg()
    if token is None:
        return jsonify({"result": "error", "error_msg": "No token given."})
    db = Database()
    remove_session(db, token)
    return jsonify({"result": "ok"})


@app.route("/user/info")
def get_user_info():
    db = Database()
    user = get_user_from_token(db)
    if user is None:
        return jsonify({"result": "error"})
    d = dictify(user, {'password', 'salt'})
    return jsonify({"result": "ok", "userinfo": d})


@app.route("/user/follow_coin")
def follow_coin():
    coin_type = get_coin_type_arg()
    # Check whether the requested coin type is valid.
    if coin_type is None:
        return jsonify({"result": "error", "error_msg": "Invalid coin type."})
    unfollow_flag = request.args.get("unfollow", type=int, default=0)
    unfollow = unfollow_flag == 1
    notify_email_flag = request.args.get("notify", type=int, default=-1)
    notify_email = notify_email_flag == 1
    db = Database()
    user = get_user_from_token(db)
    if user is None:
        return jsonify({"result": "error", "error_msg": "Invalid token."})
    followed = next(filter(lambda fc: coin_type == fc.coin_type, user.followed_coins), None)
    # Follow
    if not unfollow:
        if followed is not None and notify_email_flag >= 0:
            db.update_by("followed_coins", ["notify_email"], [1 if notify_email else 0], [MatchSelector("id", followed.id)])
            return jsonify({"result": "ok"})
        if followed is not None:
            return jsonify({"result": "error", "error_msg": "Already following."})
        # Follow the coin.
        db.create("followed_coins", [FollowedCoin(-1, user.user.id, coin_type, 1 if notify_email else 0)])
    # Unfollow
    else:
        followed = next(filter(lambda fc: coin_type == fc.coin_type, user.followed_coins), None)
        if followed is None:
            return jsonify({"result": "error", "error_msg": "Already unfollowed."})
        # Unfollow the followed coin.
        db.delete_by("followed_coins", [MatchSelector("id", followed.id)])
    return jsonify({"result": "ok"})


@app.route("/user/follow_source")
def follow_source():
    requested_source = request.args.get("source", type=str, default=None)
    # Check whether the requested source corresponds to a supported source.
    is_valid = is_valid_source(requested_source)
    if not is_valid:
        return jsonify({"result": "error", "error_msg": "No such source."})
    unfollow_flag = request.args.get("unfollow", type=int, default=0)
    unfollow = unfollow_flag == 1
    notify_email_flag = request.args.get("notify", type=int, default=-1)
    notify_email = notify_email_flag == 1
    db = Database()
    user = get_user_from_token(db)
    if user is None:
        return jsonify({"result": "error", "error_msg": "Invalid token."})
    # Get the sources the user is already following.
    followed_sources_set = set([src.__repr__() for src in user.followed_sources])
    # Follow
    followed = next(filter(lambda fc: requested_source == fc.source, user.followed_sources), None)
    if not unfollow:
        if followed is not None and notify_email_flag >= 0:
            db.update_by("followed_sources", ["notify_email"], [1 if notify_email else 0], [MatchSelector("id", followed.id)])
            return jsonify({"result": "ok"})
        # If the user is already following the source, no need to add it again.
        if followed is not None:
            return jsonify({"result": "error", "error_msg": "Already following."})
        # Follow the new source.
        db.create("followed_sources", [FollowedSource(-1, user.user.id, requested_source, 1 if notify_email else 0)])
    # Unfollow
    else:
        # Get the followed source instance.
        if followed is None:
            return jsonify({"result": "error", "error_msg": "Already unfollowed."})
        # Unfollow the followed source.
        db.delete_by("followed_sources", [MatchSelector("id", followed.id)])
    return jsonify({"result": "ok"})


if __name__ == "__main__":
    # recreate_database()
    app.run()
