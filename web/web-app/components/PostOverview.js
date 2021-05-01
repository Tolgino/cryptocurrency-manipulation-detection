import { useCallback, useState } from "react"
import { IoChatbubblesSharp, IoEllipsisHorizontal } from "react-icons/io5"
import { dateToString, getCoinIcon, getSourceColor, getSourceIcon } from "../helpers"
import { MultipurposeCard } from "./MultipurposeCard"
import { MiniImpact } from "./MiniImpact"
import { MdDateRange, MdExpandMore } from "react-icons/md"
import Link from "next/link"
import { AiOutlineArrowDown, AiOutlineArrowUp, AiOutlineEllipsis, AiOutlineLink } from "react-icons/ai"
import { FaEllipsisH } from "react-icons/fa"
import { BsChevronCompactDown } from "react-icons/bs"

const mutedColor = "gray-500"
const innerColor = "gray-850"
const innerBorderColor = "gray-800"

export const PostOverview = ({ post }) => {

  const [selected, setSelected] = useState(false)

  const getInteractionColor = useCallback((score) => {
    return (score > 1000)? "red-500"
          : (score > 500) ? "green-600" 
          : (score > 200) ? "green-500"
          : (score > 100) ? "green-300"
          : (score > 80) ? "yellow-600"
          : (score > 60) ? "yellow-500"
          : (score > 40) ? "yellow-300"
          : mutedColor

  }, [post])

  return (post &&
    <div className="my-2">
    <MultipurposeCard badgeColor={getSourceColor(post.user + '@' + post.source)} disperse={true}>
      <MultipurposeCard.Left>
        <div className={`flex flex-col px-4 py-2 w-32`}>
          <span className="font-semibold width-50 truncate hover:underline">
            <Link href={`/user-info?user=${post.user}@${post.source}`}>
              {post.user}
            </Link>
          </span>
          <div className={`py-1 flex flex-row items-center text-xs text-${mutedColor}`}>
            <span className="mr-1">
                {getSourceIcon(post.user + '@' + post.source)}
            </span>
            <span className="truncate hover:underline">
              <Link href={`/source-info?source=*@${post.source}`}>
                {post.source}
              </Link>
            </span>
          </div>
          <div className={`flex flex-row items-center text-xs text-${mutedColor}`}>
            <span className="mr-1">
              { getCoinIcon(post.coin_type) }
            </span>
            <span className={`text-xs text-${mutedColor} truncate hover:underline`}>
              <Link href={`/coin-info?coin=${post.coin_type}`}>
                { post.coin_type.toUpperCase() }
              </Link>
            </span>
          </div>
        </div>
      </MultipurposeCard.Left>
      <MultipurposeCard.Middle>
        <div className="flex flex-col px-4 py-2">
          <div 
            className={`flex flex-col justify-between ${!selected ? 'h-20 overflow-hidden' : 'min-h-20 max-h-48 overflow-scroll'} 
                        bg-${innerColor} border border-${innerBorderColor} px-4 py-2 rounded relative`}>
            <p>
              {post.content}
            </p>
            { selected && (
              <div className="text-xs text-gray-600 mt-2 hover:text-gray-200">
                  <button className="hover:underline w-full flex flex-row items-center justify-center space-x-1">
                    <AiOutlineLink />
                    <span>Go to original...</span>
                  </button>
              </div>
              )}
            { !selected &&
            <p className={`absolute left-0 right-0 bottom-0 w-full h-8 flex flex-col items-center justify-end 
                           text-transparent hover:text-white font-semibold 
                           bg-gradient-to-t from-${innerColor} 
                           ${!selected && 'cursor-pointer'}`}
                onClick={() => setSelected(!selected)}>
                <BsChevronCompactDown />
            </p> 
            }
          </div>
        </div>
      </MultipurposeCard.Middle>
      <MultipurposeCard.Right>
        <div className={`flex px-4 py-2 flex-col w-32`}>
          <div className={`px-2 py-1 flex flex-row items-center lg:justify-end text-${getInteractionColor(post.interaction)}`}>
            <span className="mr-1">
              {post.interaction}
            </span>
            <IoChatbubblesSharp />
          </div>
          <div className={`px-2 flex flex-row lg:justify-end text-${mutedColor}`}>
            <MiniImpact impact={ post.impact } />
          </div>
          <div className={`flex py-1 items-center flex-row lg:justify-end text-xs text-${mutedColor}`}>
            <span>
              {dateToString(new Date(post.time*1000))}
            </span>
          </div>
        </div>
      </MultipurposeCard.Right>
    </MultipurposeCard>
    </div>
    )
}