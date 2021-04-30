import { DashboardPanel } from "../../components/DashboardPanel";
import { SimpleDropdown } from "../../components/SimpleDropdown";
import { PostOverview } from "../../components/PostOverview";
import { getSourceIcon, getSourceParts } from "../../helpers";
import { useEffect, useMemo, useState } from "react";
import { SourceOverview } from "../../components/SourceOverview";
import { CoinOverview } from "../../components/CoinOverview";
import { FollowButton } from "../../components/FollowButton";
import { useApiData } from "../../api-hook";
import { useRequireLogin, useUser } from "../../user-hook";
import { useRouter } from "next/router";

export default function SourceInfo() {
  useRequireLogin()
  const router = useRouter()
  const sourceName = router.query.source
  // Redirect if the given sourceName does not denote a full source.
  useEffect(() => {
    if(sourceName && !sourceName.startsWith('*')) {
      router.push("/user-info?user=" + sourceName)
    }
  }, [sourceName])
  const { user, isFollowingSource } = useUser()
  // Fetch the source info and update it when the user changes.
  const sourceInfo = useApiData(null, "source_stats", { 
    source: sourceName
  }, [user, sourceName], () => sourceName != null)
  const [sortByOption, setSortByOption] = useState("interaction")
  const [sortOrderOption, setSortOrderOption] = useState("descending")
  // Fetch the posts from the source.
  const posts = useApiData([], "posts", {
    source: sourceName
  }, [sourceName], () => sourceName != null)
  const [sortedPosts, setSortedPosts] = useState([])
  // Sorter.
  useEffect(() => {
    if (posts === null || posts.length === 0) {
      setSortedPosts([]);
      return;
    }
    const sorter =
      sortByOption === "time"
        ? (a, b) => a.time - b.time
        : sortByOption === "interaction"
        ? (a, b) => a.interaction - b.interaction
        : (a, b) => ("" + a.user).localeCompare(b.user);
    const sorted = [...posts].sort(sorter);
    if (sortOrderOption === "descending") {
      sorted.reverse();
    }
    setSortedPosts(sorted);
  }, [posts, sortOrderOption, sortByOption]);
  
  return (!sourceName ? "..." :
    <div className="animate-fade-in-down grid grid-cols-12 mt-2 gap-2">
      <div className="col-start-2 col-span-2">
        <DashboardPanel collapsable={false}>
          <DashboardPanel.Header>
            <div className="grid grid-cols-1 mt-2 place-items-center">
              <span className="text-4xl">{ getSourceIcon(sourceName) }</span>
              <span className="mt-2">{ getSourceParts(sourceName)[1] }</span>
              <span className="mt-2 font-light">
                {sourceInfo?.num_followers && sourceInfo.num_followers} Followers
              </span>
              <div className="mt-2">
                <FollowButton
                  followEndpoint={"follow_source"}
                  params={{source: sourceName}}
                  isFollowing={() => isFollowingSource(sourceName)} />
              </div>
            </div>
          </DashboardPanel.Header>
          <DashboardPanel.Body></DashboardPanel.Body>
        </DashboardPanel>
        <DashboardPanel collapsable={false}>
          <DashboardPanel.Header>
            <p className="text-center">Relevant Coins</p>
          </DashboardPanel.Header>
          <DashboardPanel.Body>
            {sourceInfo?.relevant_coins && sourceInfo.relevant_coins.length > 0
              ? sourceInfo.relevant_coins.map(coin => (
                  <CoinOverview 
                    coin={coin.coin_type}
                    singleLine={true} />
                ))
              : "No Relevant Coins Found."}
          </DashboardPanel.Body>
          <DashboardPanel.Footer></DashboardPanel.Footer>
        </DashboardPanel>
      </div>
      <div className="col-start-4 col-span-6">
        <DashboardPanel collapsable={false} restrictedHeight={false}>
          <DashboardPanel.Header>
            <div className="flex items-center flex-justify-between font-normal">
              <div>
                <span>Showing all posts from </span>
                <span className="font-semibold">{sourceName.slice(2)}</span>
              </div>
              <span class="flex-grow"></span>
              <div className="flex text-xs items-center">
                <div className="flex items-center border-gray-780 mr-2 px-2">
                  <span className="">sort by</span>
                  <SimpleDropdown
                    options={["time", "interaction", "user"]}
                    selected={sortByOption}
                    setSelected={setSortByOption}
                  />
                  <span className="mx-1">in</span>
                  <SimpleDropdown
                    options={["ascending", "descending"]}
                    selected={sortOrderOption}
                    setSelected={setSortOrderOption}
                  />
                  <span className="mx-1">order</span>
                </div>
              </div>
            </div>
          </DashboardPanel.Header>
          <DashboardPanel.Body>
            {sortedPosts.length > 0 ? (
              <div className="overflow-y-auto max-h-128">
                {sortedPosts.map((post, i) => (
                  <PostOverview post={post} />
                ))}
              </div>
            ) : (
              <div className="mt-2">No posts to show.</div>
            )}
          </DashboardPanel.Body>
        </DashboardPanel>
      </div>
      <div className="col-start-10 col-span-2">
        <DashboardPanel collapsable={false}>
          <DashboardPanel.Header>
            <p>Top Interacted Users</p>
          </DashboardPanel.Header>
          <DashboardPanel.Body>
              {sourceInfo?.top_interacted_users && sourceInfo.top_interacted_users.map(user => (
                <SourceOverview
                  source={user.source}
                  button={<>{user.total_interaction}</>} 
                  singleLine={true} />
              ))}
          </DashboardPanel.Body>
        </DashboardPanel>
        <DashboardPanel collapsable={false}>
          <DashboardPanel.Header>
            <p>Top Active Users</p>
          </DashboardPanel.Header>
          <DashboardPanel.Body>
            {sourceInfo?.top_active_users && sourceInfo.top_active_users.map(user => (
                <SourceOverview
                  source={user.source}
                  button={<>{user.total_msg}</>}
                  singleLine={true} />
              ))}
          </DashboardPanel.Body>
        </DashboardPanel>
      </div>
    </div>
  );
}