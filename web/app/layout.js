import { Montserrat } from "next/font/google";
import "@/styles/globals.css";

const font = Montserrat({ subsets: ["latin"] });

export const metadata = {
  title: "Blue & Booked",
  description: "UofT Booking Bot",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={font.className}>{children}</body>
    </html>
  );
}
