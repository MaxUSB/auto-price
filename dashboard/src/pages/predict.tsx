import api from '../utils/api';
import { createStyles, makeStyles } from '@mui/styles';
import { IDictionary, TResponse } from '../utils/types';
import carForm from "../components/formGenerator/carForm";
import PredictResults from '../components/PredictResults';
import React, { FormEvent, useEffect, useState } from 'react';
import formGenerator, { IFormItem } from '../components/formGenerator';
import { Button, Grid, Stepper, Step, StepLabel, Stack, Snackbar, Backdrop, CircularProgress, Avatar, Typography, Link, Alert } from '@mui/material';

const useStyles = makeStyles(() =>
  createStyles({
    root: {
      height: '100vh',
      alignItems: 'center',
      justifyContent: 'center',
    },
    content: {
      padding: '30px',
      margin: '20px 0',
      borderRadius: '10px',
      height: 'calc(100% - 40px)',
      backgroundColor: '#FFFFFFB2',
    },
    logo: {
      gap: '20px',
      justifyContent: 'center',
    },
    formItemContainer: {
      padding: '20px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    },
    formItem: {
      width: '80%',
      backgroundColor: '#FFFFFFB2',
    },
    formSubmit: {
      padding: '40px 20px',
      justifyContent: 'center',
    },
  }),
);

const steps = ['Ввод параметров автомобиля', 'Результаты оценки стоимости'];

interface IError {
  open: boolean;
  message: string;
}

interface ICatalogs {
  cityList?: string[];
  markList?: string[];
  modelList?: string[];
  horsepowerList?: string[];
}

interface ICar {
  city?: string;
  mark?: string;
  year?: number;
  model?: string;
  owners?: number;
  mileage?: number;
  horsepower?: string;
}

interface IPredictState {
  car: ICar;
  error: IError;
  activeStep: number;
  isLoading: boolean;
  catalogs: ICatalogs;
  predictedPrice: number | null;
  predictedError: number | null;
  similarCars: any[];
}

const Predict = () => {
  const classes = useStyles();
  const [state, setState] = useState<IPredictState>({
    // car: { city: 'Тюмень', mark: 'Honda', model: 'Accord', horsepower: '190', year: 2007, mileage: 240000, owners: 4 },
    // car: { city: 'Тюмень', mark: 'Chevrolet', model: 'Aveo', horsepower: '101', year: 2011, mileage: 120000, owners: 2 },
    car: {},
    catalogs: {},
    activeStep: 0,
    isLoading: false,
    predictedPrice: null,
    predictedError: null,
    similarCars: [],
    error: { open: false, message: '' },
  });

  const reloadCatalogs = async (mark: string | undefined, model: string | undefined) => {
    const tasks = [];
    if (mark) {
      tasks.push(api('get', 'catalogs', { catalog: 'models', mark }));
    } else if (model) {
      tasks.push(api('get', 'catalogs', { catalog: 'model_params', model }));
    } else {
      tasks.push(api('get', 'catalogs', { catalog: 'marks', mark }));
      tasks.push(api('get', 'catalogs', { catalog: 'cities', mark }));
    }
    const responses = await Promise.all(tasks);
    const catalogs: IDictionary<string[]> = { ...state.catalogs };
    const errors: string[] = [];
    responses.forEach((response: TResponse) => {
      if (!response.success) {
        errors.push(response.error!);
      } else {
        Object.keys(response.data).forEach(param => {
          catalogs[`${param}List`] = response.data[param];
        });
      }
    });
    if (errors) {
      setState({ ...state, catalogs, error: { open: true, message: errors.join('\n') } });
    } else {
      setState({ ...state, catalogs });
    }
  };

  const handleCloseNotification = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason !== 'clickaway') {
      setState({ ...state, error: { ...state.error, open: false } });
    }
  };

  const handleChangeStep = (activeStep: number) => () => setState({ ...state, activeStep });

  const carFormInit: IFormItem[] = carForm(
    state.catalogs.cityList || [],
    state.catalogs.markList || [],
    state.catalogs.modelList || [],
    state.catalogs.horsepowerList || [],
  );

  const handleChange = (item: string, value: any) => setState({ ...state, car: { ...state.car, [item]: value } });

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setState({ ...state, isLoading: true });
    const data = state.car;
    const response = (await api('post', 'predict', { data })) as TResponse;
    if (!response.success) {
      setState({ ...state, isLoading: false, error: { open: true, message: String(response.error!) } });
      return;
    }
    const r_data = response.data;
    setState({ ...state, isLoading: false, activeStep: 1, predictedPrice: r_data['Price'], predictedError: r_data['PredictedError'], similarCars: r_data['Similar'] })
  };

  useEffect(() => {
    reloadCatalogs(state.car.mark, undefined);
  }, [state.car.mark]);

  useEffect(() => {
    reloadCatalogs(undefined, state.car.model);
  }, [state.car.model]);

  return (
    <Grid container className={classes.root}>
      <Grid container item xs={10} direction="column" className={classes.content}>
        <Stack spacing={5} overflow="auto">
          <Grid item xs={12}>
            <Link href="/" style={{ color: 'black', textDecoration: 'none' }}>
              <Grid item container className={classes.logo}>
                <Avatar src="logo.png" alt="Auto Price" sx={{ width: 40, height: 40 }}/>
                <Typography variant="h4" textAlign="center">auto-price</Typography>
              </Grid>
            </Link>
          </Grid>
          <Grid item xs={12}>
            <Stepper activeStep={state.activeStep}>
              {steps.map((step, num) => (
                <Step key={step} onClick={handleChangeStep(num)}>
                  <StepLabel>{step}</StepLabel>
                </Step>
              ))}
            </Stepper>
          </Grid>
          <Grid item xs={12}>
            {state.activeStep === 0 ? (
              <Grid container item xs={12} component="form" onSubmit={handleSubmit}>
                {formGenerator(carFormInit, state.car, handleChange, classes)}
                <Grid container item xs={12} className={classes.formSubmit}>
                  <Grid item xs={11}>
                    <Button variant="contained" type="submit" fullWidth size="large">Оценить</Button>
                  </Grid>
                </Grid>
              </Grid>
            ) : (
              <PredictResults
                predictedPrice={state.predictedPrice}
                predictedError={state.predictedError}
                similarCars={state.similarCars}
                mark={state.car.mark}
                model={state.car.model}
              />
            )}
          </Grid>
        </Stack>
      </Grid>
      <Backdrop open={state.isLoading}>
        <CircularProgress sx={{ color: "#23D5ABFF" }}/>
      </Backdrop>
      {state.error.message ? (
        <Snackbar open={state.error.open} autoHideDuration={4000} onClose={handleCloseNotification} anchorOrigin={{ vertical: "top", horizontal: "left" }}>
          <Alert variant="filled" severity="error">{state.error.message}</Alert>
        </Snackbar>
      ): null}
    </Grid>
  );
}

export default Predict;
