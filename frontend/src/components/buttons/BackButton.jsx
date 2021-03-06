import { GoBackButton } from '../styledComponents/index';
import { useHistory } from 'react-router-dom';

export const BackButton = () => {
  let history = useHistory();
  const goToPreviousPath = () => {
    history.goBack();
  };
  return (
    <div className="p-0 d-flex justify-content-center align-items-center button">
      <GoBackButton
        onClick={goToPreviousPath}
        className="d-flex justify-content-center align-items-center"
      >
        <svg
          className="l-arrow"
          width="9"
          height="14"
          viewBox="0 0 9 14"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M8 1L2 7L8 13"
            stroke="#195669"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </svg>
      </GoBackButton>
    </div>
  );
};
