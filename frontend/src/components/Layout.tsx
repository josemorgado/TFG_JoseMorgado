import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";
import "./Layout.css"
const Layout: React.FC = () => {

console.log("LAYOUT RENDERED");

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