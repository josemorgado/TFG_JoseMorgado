interface PageErrorProps {
  message: string;
}

export default function PageError({ message }: PageErrorProps) {
  return (
    <div className="page-center">
      <div className="page-center__content">
        <div className="page-message page-message--error">
          {message}
        </div>
      </div>
    </div>
  );
}