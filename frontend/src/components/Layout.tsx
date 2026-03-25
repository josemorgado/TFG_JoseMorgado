import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";
import Footer from "./Footer";
import "../styles/Layout.css"
const Layout: React.FC = () => {

console.log("LAYOUT RENDERED");

  return (
    <>
      <div className="layout">
        <Navbar />
        <main className="content">
            <Outlet />
        </main>
        <Footer/>
      </div>
    </>
  );
};

export default Layout;