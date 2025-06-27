import React from "react";

export function TestLanding() {
  return (
    <div style={{ 
      padding: "20px", 
      backgroundColor: "#000", 
      color: "#fff", 
      minHeight: "100vh" 
    }}>
      <h1>VyralFlow AI - Test Page</h1>
      <p>If you can see this, React is working!</p>
      <button onClick={() => alert("Button clicked!")}>
        Test Button
      </button>
    </div>
  );
}