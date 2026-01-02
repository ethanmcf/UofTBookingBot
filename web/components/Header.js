import Logo from "@/images/robot-icon.png";
import Button from "@/components/Button";
import Image from "next/image";
import ScrollLink from "@/components/ScrollLink";
export default function Header() {
  return (
    <div
      className={
        "lg:max-w-6xl w-full items-center justify-between flex text-tBlack "
      }
    >
      <ScrollLink to={"#home"}>
        <button
          className={
            "flex w-fit items-center hover:scale-95 transform duration-100 "
          }
        >
          <Image src={Logo} alt={"Logo"} className="w-8 h-8" />
          <text className={"font-semibold text-3xl pl-2"}>Blue & Booked </text>
        </button>
      </ScrollLink>

      <div className={"flex "}>
        <div
          className={
            "hidden md:hidden lg:flex items-center space-x-6 text-xl text-tBlack"
          }
        >
          <ScrollLink to={"#home"}>
            <button className={"hover:text-primary"}>Home</button>
          </ScrollLink>
          <ScrollLink to={"#download"}>
            <Button>Download</Button>
          </ScrollLink>
        </div>
      </div>
    </div>
  );
}
