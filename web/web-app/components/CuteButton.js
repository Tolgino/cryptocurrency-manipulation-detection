const defaultTextColor = "gray-200"
const defaultColor = "gray-780"
const defaultHoverColor = "gray-850"
const borderColor = "gray-900"
const hoverBorderColor = "gray-780"

export const CuteButton = ({ size = 'xs', onClick = () => {}, isDisabled = () => false, 
                              color = defaultColor, 
                              hoverColor = defaultHoverColor, 
                              textColor = defaultTextColor,
                              width = null,
                              children }) => {
  return (
    <button
      className={`py-1 px-3 text-${size} text-${textColor} ${width != null && `w-${width}`} border border-${borderColor} rounded bg-${color} 
                hover:bg-${hoverColor} hover:border-${hoverBorderColor} 
                disabled:cursor-not-allowed disabled:opacity-50`}
      onClick={onClick}
      disabled={isDisabled()}>
    { children }
  </button>
  )
}