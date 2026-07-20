import { useLogto } from "@logto/react";

export const SignIn = () => {
  const { signIn, signOut, isAuthenticated } = useLogto();

  return isAuthenticated ? (
    <button onClick={() => signOut("http://localhost:5173")}>Sign Out</button>
  ) : (
    <button onClick={() => signIn("http://localhost:5173/callback")}>
      Sign In
    </button>
  );
};

// n3fcP4t0
