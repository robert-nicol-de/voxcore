interface RiskItemProps {
  id: number;
  title: string;
  desc: string;
}

export const RiskItem = ({ id, title, desc }: RiskItemProps) => {
  return (
    <div>
      <span className="text-blue-400">
        {id}. {title}
      </span>{" "}
      {desc}
    </div>
  );
};
