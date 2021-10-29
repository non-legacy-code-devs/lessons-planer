import React from 'react';
import { Wrapper } from '../components/styledComponents/index';
import { BackButton } from '../components/buttons/BackButton';

export const InactiveReplacement = () => {
  return (
    <div className="min-h-100 py-5 py-lg-0 d-flex flex-column justify-content-center align-items-center">
      <div className="d-flex justify-content-center mb-5">
        <BackButton />
        <h1 className="title">Przepraszamy</h1>
      </div>
      <Wrapper>
        <p className="text">Zastępstwo nieaktywne</p>
      </Wrapper>
    </div>
  );
};
