
import { useCallback, useEffect, useState } from "react"
import { IoChatbubblesSharp } from "react-icons/io5"
import { FiDollarSign } from "react-icons/fi"
import { getCoinColor, getCoinIcon } from "../Helpers"
import axios from "axios"
import { CuteButton } from "./CuteButton"
import { MultipurposeCard } from "./MultipurposeCard"
import Link from "next/link"

const mutedTextColor = "gray-500"
const bgColor = "gray-850"


export const CoinOverview = ({ coin, button, singleLine = false }) => {

  const [coinInfo, setCoinInfo] = useState(null)

  // TODO parametrize!
  useEffect(() => {
    axios.get("http://127.0.0.1:5000/api/coin_info?type=" + coin)
      .then(resp => {
        console.log(resp.data)
        setCoinInfo(resp.data)
      })
  }, [coin])

  return (
    <MultipurposeCard badgeColor={getCoinColor(coin)} colorizer={() => bgColor}>
      <MultipurposeCard.Left>
        <span className={`text-4xl text-${getCoinColor(coin)}`}>
          {getCoinIcon(coin)}
        </span>
      </MultipurposeCard.Left>
      <MultipurposeCard.Middle>
        <div className={`flex flex-col`}>
          <div className={`py-1 flex flex-row items-center text-md`}>
            <span className="hover:underline">
              <Link href={`/coin-info?coin=${coin}`}>
                {coin.toUpperCase()}
              </Link>
            </span>
          </div>
          { !singleLine && (
            <div className={`flex flex-row items-center text-xs text-${mutedTextColor}`}>
              <span className="mr-1">
                <FiDollarSign />
              </span>
              <span className={`text-xs text-${mutedTextColor} font-mono`}>
                { (coinInfo && coinInfo.last_price) ? (
                  coinInfo.last_price.price.toPrecision(5)
                ) : ("-")}
              </span>
            </div>
          )}
        </div>
      </MultipurposeCard.Middle>
      <MultipurposeCard.Right>
        <div>
          { button }
        </div>
      </MultipurposeCard.Right>
    </MultipurposeCard>
    )
}
