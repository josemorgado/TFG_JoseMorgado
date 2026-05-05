interface PageInfoProps {
  message: string;
}

export default function PageInfo({ message }: PageInfoProps) {
  return (
    <div className="page-center">
      <div className="page-center__content">
        <div className="page-message page-message--info">
          {message}
        </div>
      </div>
    </div>
  );
}