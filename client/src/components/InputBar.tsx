import { useState } from "react"

interface InputBarProps {
  currentMessage: string;
  setCurrentMessage: (message: string) => void;
  onSubmit: (e: React.FormEvent) => void;
}

const InputBar = ({ currentMessage, setCurrentMessage, onSubmit }: InputBarProps) => {

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setCurrentMessage(e.target.value)
    }

    return (
        <form onSubmit={onSubmit} className="p-4">
            <div className="flex items-center bg-[#F9F9F5] rounded-full p-3 shadow-md border border-gray-200">
                <input
                    type="text"
                    placeholder="Type a message"
                    value={currentMessage}
                    onChange={handleChange}
                    className="flex-grow px-4 py-2 bg-transparent focus:outline-none text-gray-700"
                />
                <button
                    type="submit"
                    className="bg-gradient-to-r from-[#7d5454] to-[#9b6c6c] hover:from-[#9b5f5f] hover:to-[#ce7c7c] rounded-full p-3 ml-2 shadow-md transition-all duration-200 group"
                >
                    <svg className="w-6 h-6 text-white transform rotate-45 group-hover:scale-110 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                    </svg>
                </button>
            </div>
        </form>
    )
}

export default InputBar