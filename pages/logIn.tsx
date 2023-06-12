import { useRouter } from 'next/router';
import { useState, FormEvent } from 'react';
import { setCookie } from 'nookies';

export let name = ""; 

function LoginPage() {
  const [localName, setLocalName] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (localName !== "") {
      setCookie(null, 'isLoggedIn', 'true', {
        maxAge: 10, // time before cookie destructs in seconds
        path: '/',
      });

      try {
        const response = await fetch('/api/clientAPI', {
          method: 'POST',
          body: JSON.stringify({ message: `User ${localName} logged in` }),
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const data = await response.json();
          console.log(data); // Log the response data if needed
        } else {
          throw new Error('Error logging the message');
        }
      } catch (error) {
        console.error(error);
      }

      name = localName; // Assign localName to the exported name variable
      router.push("/"); //homepage redirection
    } else {
      alert("Please enter your name!");
    }
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh", flexDirection: "column" }}>
      <h1 style={{ textAlign: "center", marginTop: "15px" }}>Please Enter Your Name to Continue</h1>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        <input
          type="text"
          placeholder="Enter your name"
          value={localName}
          onChange={(e) => setLocalName(e.target.value)}
          style={{ padding: "10px" }}
        />
        <button type="submit" style={{ backgroundColor: "green", color: "white", padding: "10px", border: "none", cursor: "pointer" }}>Login</button>
        <button type="button" style={{ backgroundColor: "green", color: "white", padding: "10px", border: "none", cursor: "pointer" }}>Login with Google</button>
      </form>
    </div>
  );
}

export default LoginPage;
