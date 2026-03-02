import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";

const Layout: React.FC = () => {
  return (
    <>
      <div className="layout">
        <Navbar />
        <main className="content">
            <Outlet />
        </main>
      </div>
    </>
  );
};

export default Layout;