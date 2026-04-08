export default function StepWelcome({ next }) {
  return (
    <>
      <h2 className="text-2xl mb-4 font-bold">Welcome to VoxQuery!</h2>
      <p className="mb-6">Let's get you set up in just a few steps.</p>
      <button onClick={next} className="bg-neon-green px-4 py-2 rounded">Get Started</button>
    </>
  );
}
