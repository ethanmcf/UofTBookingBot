"use client";
import React, { useEffect, useState } from "react";
const MovingDiv = (props) => {
  const [scrollOffset, setScrollOffset] = useState(0);

  const handleScroll = () => {
    setScrollOffset(window.scrollY);
  };

  useEffect(() => {
    window.addEventListener("scroll", handleScroll);
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  const moveAmount = Math.min(scrollOffset / 5, 40);
  return (
    <div
      className={""}
      style={{
        transform: `translateX(${props.leftToRight ? "-" : ""}${moveAmount}px)`,
        transition: "transform 0.5s ease-out",
      }}
    >
      {props.children}
    </div>
  );
};

export default MovingDiv;
