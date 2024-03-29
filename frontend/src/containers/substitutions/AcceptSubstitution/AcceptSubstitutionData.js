// react
import React from 'react';
// utils
import {
  Container,
  BlueButton,
  TextField,
} from '../../../components/styledComponents';
// propTypes
import PropTypes from 'prop-types';

export const AcceptSubstitutionData = ({
  substitutionData,
  takeSubstitution,
}) => {
  AcceptSubstitutionData.propTypes = {
    substitutionData: PropTypes.shape({
      id: PropTypes.number,
      datetime: PropTypes.string,
      new_teacher_found: PropTypes.bool,
      last_topics: PropTypes.string,
      planned_topics: PropTypes.string,
      methodology_and_platform: PropTypes.string,
      old_teacher: PropTypes.number,
      level: PropTypes.number,
      subject: PropTypes.number,
      new_teacher: PropTypes.number,
    }),
    takeSubstitution: PropTypes.func.isRequired,
  };

  const handleSubmit = (id) => {
    let sub_id = id.toString();
    takeSubstitution(sub_id);
  };

  const capitalizeName = (name) => {
    return name.charAt(0).toUpperCase() + name.slice(1);
  };

  return (
    <div className="col-12">
      {substitutionData ? (
        <Container>
          <div className="row text mb-4">
            <p className="text-center">
              {substitutionData?.subject_name
                ? capitalizeName(substitutionData?.subject_name)
                : substitutionData?.subject}{' '}
              w dniu{' '}
              {substitutionData?.datetime
                .split('T')[0]
                .replaceAll('-', '.')
                .split('.')
                .reverse()
                .join('.')}
            </p>
          </div>
          <div className="row mb-4">
            <div className="col-12 col-xl-4 d-flex justify-content-center flex-column mb-4 mb-xl-0">
              <p className="text">Klasa</p>
              <TextField>{substitutionData?.level_name}</TextField>
            </div>
            <div className="col-12 col-xl-4 d-flex justify-content-center flex-column mb-4 mb-xl-0">
              <p className="text">Data</p>
              <TextField>
                {substitutionData?.datetime.split('T')[0].replaceAll('-', '.') +
                  ' / ' +
                  substitutionData?.datetime
                    .split('T')[1]
                    .split('+')[0]
                    .split(':')[0] +
                  ':' +
                  substitutionData?.datetime
                    .split('T')[1]
                    .split('+')[0]
                    .split(':')[1]}
              </TextField>
            </div>
            <div className="col-12 col-xl-4 d-flex justify-content-center flex-column">
              <p className="text">Przedmiot</p>
              <TextField>{substitutionData?.subject_name}</TextField>
            </div>
          </div>
          <div className="col d-flex flex-column justify-content-center">
            <p className="text">Ostatnio przerabiane zagadnienia</p>
            <TextField>
              {substitutionData?.last_topics
                ? substitutionData?.last_topics
                : 'Nie podano.'}
            </TextField>
          </div>
          <div className="col d-flex flex-column mt-4 justify-content-center">
            <p className="text">Planowane zagadnienia na lekcję</p>
            <TextField>
              {substitutionData?.planned_topics
                ? substitutionData?.planned_topics
                : 'Nie podano.'}
            </TextField>
          </div>
          <div className="col d-flex flex-column mt-4 justify-content-center">
            <p className="text">Metodyka nauczania oraz platforma</p>
            <TextField>
              {substitutionData?.methodology_and_platform
                ? substitutionData?.methodology_and_platform
                : 'Brak danych.'}
            </TextField>
          </div>
          <div className="col d-flex mt-4 justify-content-center">
            <BlueButton
              role="button"
              onClick={() => handleSubmit(substitutionData.id)}
            >
              akceptuj
            </BlueButton>
          </div>
        </Container>
      ) : (
        <div className="col-12">
          <Container>
            <div className="row">
              <p className="text-center title">Brak danych do wyświetlenia</p>
            </div>
            <div className="row justify-content-center">
              <p className="text-right text w-50 mt-5">
                Może to być błąd przy pobieraniu danych z serwera. Odśwież
                stronę, aby spróbować ponownie.
              </p>
            </div>
          </Container>
        </div>
      )}
    </div>
  );
};

export default AcceptSubstitutionData;
