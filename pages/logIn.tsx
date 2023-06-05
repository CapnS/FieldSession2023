import { useRouter } from 'next/router';
import { useState, FormEvent } from 'react';
import { setCookie } from 'nookies';

function LoginPage() {
    const [name, setName] = useState("");
    const router = useRouter();

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        if (name !== "") {
            setCookie(null, 'isLoggedIn', 'true', {
                maxAge: 10, // time before cookie destructs in seconds
                path: '/',
            });
            router.push("/"); //homepage redirection
        } else {
            alert("Please enter your name!");
        }
    };

    return (
        <div style={{display: "flex", justifyContent: "center", alignItems: "center", height: "100vh", flexDirection: "column"}}>
            <h1 style={{textAlign: "center", marginTop: "15px"}}>Please Enter Your Name to Continue</h1>
            <form onSubmit={handleSubmit} style={{display: "flex", flexDirection: "column", gap: "10px"}}>
                <input
                    type="text"
                    placeholder="Enter your name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    style={{padding: "10px"}}
                />
                <button type="submit" style={{backgroundColor: "green", color: "white", padding: "10px", border: "none", cursor: "pointer"}}>Login</button>
                <button type="button" style={{backgroundColor: "green", color: "white", padding: "10px", border: "none", cursor: "pointer"}}>Login with Google</button>
            </form>
        </div>
    );
}

export default LoginPage;
