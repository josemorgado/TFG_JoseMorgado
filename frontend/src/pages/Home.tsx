import LoginButton from "../components/LoginButton";
import LogoutButton from "../components/LogoutButton";
import CreateAccountButton from "../components/CreateAccountButton";

const Home = () => {
  return (
    <div>
      <h1>Buenos dias primaches</h1>
      <LoginButton/>
      <LogoutButton/>
      <CreateAccountButton/>
    </div>
  );
};

export default Home;
