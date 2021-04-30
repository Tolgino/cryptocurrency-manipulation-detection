import axios from "axios";
import { useEffect, useState } from "react";
import { useCookies } from "react-cookie";
import { useRouter } from "next/router"
import { useRequireGuest } from "../../user-helpers"

export default function Login() {
  useRequireGuest()
  const router = useRouter()
  const [cookie, setCookie] = useCookies()

  useEffect(() => {
    if(!router) return
    setUsername(router.query.username)
  }, [router])

  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [usernameErrorMsg, setUsernameErrorMsg] = useState("")
  const [passwordErrorMsg, setPasswordErrorMsg] = useState("")

  const [errorMsg, setErrorMsg] = useState("")
  const [successMsg, setSuccessMsg] = useState("")

  const [canSubmit, setCanSubmit] = useState(false)
  const [isLoading, setLoading] = useState(false)

  const submitLogin = async (e) => {
    e.preventDefault()
    setErrorMsg("")
    setLoading(true)
    var signIn = new FormData()
    signIn.append("username", username)
    signIn.append("password", password)
    const res = await axios.post("//127.0.0.1:5000/user/login", signIn)
    if(res.data.result === "error" && res.data.error_type === 1) {
      setLoading(false)
      setUsernameErrorMsg(res.data.error_msg)
    } else if(res.data.result === "error" && res.data.error_type === 2) {
      setLoading(false)
      setPasswordErrorMsg(res.data.error_msg)
    } else if(res.data.result === "error") {
      setLoading(false)
      setErrorMsg(res.data.error_msg)
    } else if(res.data.result == "ok") {
      setCookie("token", res.data.token)
      setSuccessMsg("Success. Redirecting...")
      router.push("/dashboard")
    }
  }

  // User can submit checker.
  useEffect(() => {
    const c = (username !== "" && password !== "" && errorMsg === "" 
                && usernameErrorMsg === "" && passwordErrorMsg === "")
    setCanSubmit(c)
  }, [username, password, errorMsg, usernameErrorMsg, passwordErrorMsg])

  // Reset the error message.
  useEffect(() => {
    setUsernameErrorMsg("")
    setPasswordErrorMsg("")
  }, [username, password])

  return (
    <div className="min-h-screen flex flex-col animate-fade-in-down">
      <div className="p-5 md:p-0 mx-auto md:w-full md:max-w-md">
        <div className="px-5 py-7">
          <div className="rounded-t-lg bg-white py-5 px-5 shadow-lg">
              <h1 className="font-bold text-center text-2xl">
                Welcome back!
              </h1>
          </div>
          <form class="bg-gray-50 rounded-b-lg border-t border-b border-gray-200 pt-6 px-6 shadow-lg" onSubmit={submitLogin}>
          { (successMsg !== '') ? 
            <div class="animate-fade-in-down bg-green-100 border border-green-400 text-sm text-green-700 px-4 py-3 mb-3 rounded relative" role="alert">
              {successMsg}
            </div>
          : null}
          { (errorMsg !== '') ? 
            <div class="animate-fade-in-down bg-red-100 border border-red-400 text-sm text-red-700 px-4 py-3 mb-3 rounded relative" role="alert">
              {errorMsg}
            </div>
          : null}
            <div class="pb-8">
              <div class="mb-4">
                <label className="block text-gray-700 text-md font-bold mb-2">
                  Username
                  <input
                    type="text"
                    placeholder="Your username"
                    disabled={isLoading}
                    value={username}
                    onChange={e => setUsername(e.currentTarget.value)}
                    className={`mt-1 shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight
                          ${ usernameErrorMsg !== '' ? 'border-red-500' : null}`}
                  />
                </label>
                <p class="text-red-500 text-xs italic mt-2 ml-1">{usernameErrorMsg}</p>
              </div>
              <div class="mb-4">
                <label class="block text-gray-700 text-md font-bold mb-2">
                  Password
                  <input
                    type="password"
                    placeholder="Your password"
                    disabled={isLoading}
                    value={password}
                    onChange={e => setPassword(e.currentTarget.value)}
                    className={`mt-1 shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight
                          ${ passwordErrorMsg !== '' ? 'border-red-500' : null}`}
                  />
                </label>
                <p class="text-red-500 text-xs italic mt-2 ml-1">{passwordErrorMsg}</p>
              </div>
              <div className="grid grid-cols-2">
                <button 
                  type="submit" 
                  disabled={!canSubmit || isLoading}
                  class="bg-yellow-50 text-blue-50 h-10 py-2 px-4 w-36 rounded disabled:opacity-50 hover:bg-yellow-500">
                {isLoading ? 
                  <svg class="animate-spin m-auto w-5 h-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg> 
                : 'Log in'}
                </button>
                <a class="link inline-block text-right font-bold text-sm text-blue hover:text-blue-darker" href="#">
                  Forgot Password?
                </a>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}