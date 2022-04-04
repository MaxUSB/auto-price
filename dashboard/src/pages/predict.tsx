import React from 'react';
import {CurrencyRuble} from '@mui/icons-material'
import {createStyles, makeStyles} from "@mui/styles";
import {Button, Grid, Stepper, Step, StepLabel, Theme} from '@mui/material'

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      height: '100vh',
      alignItems: 'center',
      justifyContent: 'center',
    },
    content: {
      margin: '20px 0',
      padding: '30px',
      borderRadius: '10px',
      height: 'calc(100% - 40px)',
      backgroundColor: 'rgba(255, 255, 255, 0.7)',
    },
  }),
);

const steps = ['Ввод параметров автомобиля', 'Результаты оценки стоимости'];

const Predict = () => {
  const classes = useStyles();

  return (
    <Grid container className={classes.root}>
      <Grid container item xs={10} direction="column" className={classes.content}>
        <Grid item xs={12}>
          <Stepper>
            {steps.map(step => (
              <Step key={step}>
                <StepLabel>{step}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </Grid>
      </Grid>
    </Grid>
  );
}

export default Predict;
