interface PageEmptyProps {
  message: string;
}

export default function PageEmpty({ message }: PageEmptyProps) {
  return (
    <div className="page-center">
      <div className="page-center__content">
        <div className="page-message page-message--empty">
          {message}
        </div>
      </div>
    </div>
  );
}