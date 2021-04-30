import axios from "axios";
import { useRouter } from "next/router";
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { useCookies } from "react-cookie";

// Create the context.
const UserContext = createContext()

// The provider component.
export const UserProvider = ({ children }) => {
  // Populate the context.
  const user = useUserProvider()
  return <UserContext.Provider value={user}>{children}</UserContext.Provider>
}

// Any descendant of AuthProvider component will have access to the authentication context.
// The authentication context is simply a global hook.
export const useUser = () => useContext(UserContext)

// Represents an unauthenticated user.
const guestUser = {
  followed_coins: [],
  followed_sources: [],
  user: {
    id: -1,
    username: "guest"
  }
}
// Custom Hook to get user info.
const useUserProvider = () => {
  const [cookies, setCookie, removeCookie] = useCookies(['token'])
  const [user, setUser] = useState(null)

  // Fetch the user (for internal use)
  const fetchUser = useCallback(() => {
    axios.get('http://127.0.0.1:5000/user/info', {
      params: {
        token: cookies["token"]
      }
    }).then(res => {
      if(res && res.data && res.data.result === "ok") {
        setUser(res.data.userinfo)
      } else {
        removeCookie("token")
        setUser(guestUser)
      }
    })
  }, [cookies])

  // Update the user with the given parameters.
  const updateUser = useCallback((endpoint, params) => {
    axios.get("http://127.0.0.1:5000/user/" + endpoint, {
      params: {
        token: cookies["token"],
        ...params
      }
    }).then(res => {
      if(res && res.data && res.data.result === "ok") {
        fetchUser() 
      }
    })
  }, [cookies])

  //
  const isFollowingSource = useCallback((sourceName) => {
    if(!user) return false
    return user.followed_sources.some((followedSource) => followedSource.source.includes(sourceName))
  }, [user])

  //
  const isFollowingCoin = useCallback((coinName) => {
    if(!user) return false
    return user.followed_coins.some((followedCoin) => followedCoin.coin_type.includes(coinName))
  }, [user])

  // Run on render.
  useEffect(fetchUser, [cookies])
  // Expose data and methods.
  return { user: user, updateUser: updateUser, isFollowingSource: isFollowingSource, isFollowingCoin: isFollowingCoin }
}

// Custom Hook to redirect to the login page if needed.
export const useRequireLogin = () => {
  const { user } = useUser()
  const router = useRouter()
  useEffect(() => {
    if(user && user.user.id < 0) {
      router.push("/login")
    }
  }, [user, router])
}

// Custom Hook to redirect to the dashboard page if needed.
export const useRequireGuest = () => {
  const { user } = useUser()
  const router = useRouter()
  useEffect(() => {
    console.log(user)
    if(user && user.user.id >= 0) {
      router.push("/dashboard")
    }
  }, [user, router])

}