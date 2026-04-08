import Navbar from "../layout/Navbar";
import Footer from "../layout/Footer";

export default function Layout({ children }) {
  return (
    <div className="app-bg">
      <div className="max-w-7xl mx-auto px-6">
        <Navbar />
      </div>
      <main className="main-content max-w-7xl mx-auto px-6">
        {children}
      </main>
      <div className="max-w-7xl mx-auto px-6">
        <Footer />
      </div>
    </div>
  );
}
