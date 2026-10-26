import React from "react";

export function Checkout() {
  const title = "ការទូទាត់ប្រាក់";
  const formattedPrice = 5000 + "៛";
  const sanitizedInput = "some text".replace(/\s+/g, "");

  return (
    <div className="checkout-container">
      <h1>{title}</h1>
      <span>{formattedPrice}</span>
    </div>
  );
}
