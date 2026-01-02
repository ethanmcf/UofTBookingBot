"use client";
import React from "react";

const ScrollLink = ({ to, children }) => {
  const handleClick = (e) => {
    e.preventDefault();

    const target = document.querySelector(to);
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <a href={to} onClick={handleClick}>
      {children}
    </a>
  );
};

export default ScrollLink;
