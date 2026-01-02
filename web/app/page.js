import Result1 from "@/images/ResultsScreen1.png";
import Result2 from "@/images/ResultsScreen2.png";
import DownloadCard from "@/components/Download";
import Header from "@/components/Header";
import Button from "@/components/Button";
import Image from "next/image";
import ScrollLink from "@/components/ScrollLink";
import MovingDiv from "@/components/MovingDiv";

export default function Home() {
  return (
    <main className="flex min-h-screen items-center flex-col pl-2 pr-2 pt-10 md:pl-10 md:pr-10">
      <Header />
      {/*Home page*/}
      <div
        className={
          "lg:pt-64 pt-40 lg:max-w-6xl w-full lg:w-full flex flex-col lg:flex-row"
        }
        id={"home"}
      >
        {/*Info section*/}
        <div
          className={
            "flex-col flex-1 text-center sm:text-left space-y-3 justify-center flex"
          }
        >
          <div
            className={"font-bold text-[2.5rem] leading-10 space-y-1 text-wrap"}
          >
            <h1>We are automating the campus experience,</h1>
            <h1 className={"text-wrap"}></h1>
          </div>
          <h2 className={"text-lg text-wrap"}>
            UofT Booking Bot is committed to securing the best activity spots
            for you.
          </h2>
          <div className={"justify-center sm:justify-start flex space-x-3"}>
            <ScrollLink to={"#download"}>
              <Button>Download </Button>
            </ScrollLink>
          </div>
        </div>
        {/*Bubble section*/}
        <div
          className={
            "relative mt-40 lg:mt-0 h-80 lg:w-[40rem] m-w-full w-full overflow-x-clip"
          }
        >
          <div
            className={
              "flex w-full h-full absolute items-center justify-center"
            }
          >
            <div
              className={
                "left-1/2 top-1/2 w-4/12 h-full bg-gradient-to-t from-blue-300 to-purple-200 blur-2xl"
              }
            />
            <div
              className={
                "left-1/2 top-1/2 w-4/12 h-full bg-gradient-to-b from-blue-300 to-blue-200 blur-2xl"
              }
            />
          </div>
          <MovingDiv leftToRight={true}>
            <Image
              src={Result2}
              alt={"result1"}
              className={
                "rounded-xl w-[20rem] sm:w-[25rem] absolute top-32 right-1 md:right-1/3 lg:right-1/4 shadow-xl"
              }
            />
          </MovingDiv>
          <MovingDiv leftToRight={false}>
            <Image
              src={Result1}
              alt={"result2"}
              className={
                "rounded-xl w-[20rem] sm:w-[25rem] h-auto absolute left-1 md:left-1/3 lg:left-1/4 -top-20 shadow-xl"
              }
            />
          </MovingDiv>
        </div>
      </div>

      {/*Download page*/}
      <div
        className={
          "pt-64 lg:pb-64 pb-24 lg:w-full flex flex-col items-center text-center"
        }
      >
        <hr className="w-full max-w-6xl h-0.5 bg-gray-200 rounded-full" />
        <div
          className={"lg:pt-32 lg:max-w-6xl w-full flex flex-col items-center"}
          id={"download"}
        >
          <div className={"space-y-8 w-full"}>
            <div className={"text-center space-y-4"}>
              <h1 className={"font-bold text-[2rem]"}>Download</h1>
              <h2 className={"text-md text-wrap max-w-2xl mx-auto"}>
                Download corresponding to your system specs.
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto p-6">
              <DownloadCard platform="windows" />
              <DownloadCard platform="macOS" />
              <DownloadCard platform="linux" />
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
