export default function ProfilePage() {
  return (
    <div className="p-4 md:p-8">
      <h1 className="text-2xl font-bold">User Profile</h1>
      <div className="mt-8 grid grid-cols-3 gap-1 md:gap-4">
        {/* Instagram style grid placeholder */}
        {[1,2,3,4,5,6].map(i => (
          <div key={i} className="aspect-square bg-accent hover:opacity-90 cursor-pointer object-cover">
          </div>
        ))}
      </div>
    </div>
  );
}
