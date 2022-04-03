import './predict.css';
import React from 'react';
import {CurrencyRuble} from '@mui/icons-material'
import {Button, Grid, Stepper, Step, StepLabel} from '@mui/material'

const steps = ['Введите параметры автомобиля', 'Результаты оценки'];

const Predict = () => {
  return (
    <Grid container className="root">
      <Grid container item xs={10} direction="column" className="content">
        <Stepper>
          {steps.map(step => (
            <Step key={step}>
              <StepLabel>{step}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Grid>
    </Grid>
  );
}

export default Predict;
