"use client";
import Arrow from "@/svgs/download-solid-full.svg";
import Image from "next/image";

export default function Button(props) {
  return (
    <button
      className={
        "bg-primary text-white w-fit h-14 flex items-center pl-10 pr-10 " +
        "rounded-full shadow-xl shadow-blue-100 hover:scale-95 transform duration-100 group"
      }
    >
      <text className={"font-bold text-lg"}>{props.children}</text>
      <Image
        src={Arrow}
        alt={"arrow"}
        className={
          "ml-2 h-5 w-5 group-hover:translate-x-2 transform duration-150 text:white"
        }
      />
    </button>
  );
}
