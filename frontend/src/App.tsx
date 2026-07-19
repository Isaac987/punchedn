import { SignIn } from "./SignIn";
import { useLogto, type IdTokenClaims } from "@logto/react";
import { useEffect, useState } from "react";

export const App = () => {
  const { getAccessToken, isAuthenticated, getIdTokenClaims } = useLogto();
  const [user, setUser] = useState<IdTokenClaims>();

  useEffect(() => {
    (async () => {
      if (isAuthenticated) {
        const claims = await getIdTokenClaims();
        const token = await getAccessToken("https://dev.punchedn.com/api");
        console.log(token);
        setUser(claims);
      }
    })();
  }, [getIdTokenClaims, isAuthenticated]);

  return (
    <>
      <h1>This is PunchedN!</h1>

      <SignIn />

      {isAuthenticated && user && (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Value</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(user).map(([key, value]) => (
              <tr key={key}>
                <td>{key}</td>
                <td>
                  {typeof value === "string" ? value : JSON.stringify(value)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
};

export default App;
