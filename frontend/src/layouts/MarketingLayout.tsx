import Header from "../components/layout/Header";
import Footer from "../components/layout/Footer";

export default function MarketingLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-[#0a1830] to-[#07111f] text-white">
      <Header />
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 py-8">{children}</main>
      <Footer />
    </div>
  );
}
