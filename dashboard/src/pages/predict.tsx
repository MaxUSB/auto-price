import api from '../utils/api';
import {createStyles, makeStyles} from '@mui/styles';
import {IDictionary, TResponse} from '../utils/types';
import carForm from "../components/formGenerator/carForm";
import React, {ChangeEvent, FormEvent, useEffect, useState} from 'react';
import formGenerator, {IFormItem} from "../components/formGenerator";
import {Button, Grid, Stepper, Step, StepLabel, Stack, Snackbar, Alert, Backdrop, CircularProgress, Avatar, Typography} from '@mui/material'

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
  }),
);

const steps = ['Ввод параметров автомобиля', 'Результаты оценки стоимости'];

interface IError {
  open: boolean;
  message: string;
}

interface ICatalogs {
  hpList?: number[];
  cityList?: string[];
  markList?: string[];
}

interface ICar {
  hp?: number;
  mark?: string;
  city?: number;
  year?: number;
  pts?: string;
  owners?: number;
  mileage?: number;
  fuelType?: string;
  gearType?: string;
  transmission?: string;
}

interface IPredictState {
  car: ICar;
  error: IError;
  activeStep: number;
  isLoading: boolean;
  catalogs: ICatalogs;
}

const Predict = () => {
  const classes = useStyles();
  const [state, setState] = useState<IPredictState>({
    car: {},
    catalogs: {},
    activeStep: 0,
    isLoading: false,
    error: {open: false, message: ''},
  });

  const reloadCatalogs = async (mark: string | undefined) => {
    const tasks = [];
    if (mark) {
      tasks.push(api('get', 'catalogs', {catalog: 'mark_params', mark}));
    } else {
      tasks.push(api('get', 'catalogs', {catalog: 'marks', mark}));
      tasks.push(api('get', 'catalogs', {catalog: 'cities', mark}));
    }
    const responses = await Promise.all(tasks);
    const catalogs: IDictionary<any[]> = {...state.catalogs};
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
      setState({...state, catalogs, error: {open: true, message: errors.join('\n')}});
    } else {
      setState({...state, catalogs});
    }
  };

  // const handleCloseNotification = (event?: React.SyntheticEvent | Event, reason?: string) => {
  //   if (reason !== 'clickaway') {
  //     setState({...state, error: {...state.error, open: false}});
  //   }
  // };

  const handleChangeStep = (activeStep: number) => () => setState({...state, activeStep});

  const carFormInit: IFormItem[] = carForm(
    state.catalogs.cityList || [],
    state.catalogs.markList || [],
    state.catalogs.hpList || [],
  );

  const handleChange = (item: string) => (event: ChangeEvent<HTMLInputElement>, customValue?: any) => {
    const {value} = event.target || {};
    let newValue = customValue || value;
    setState({...state, car: {...state.car, [item]: newValue}});
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setState({...state, isLoading: true});
    const data = {'mark': 'Honda'}; //TODO get data from form
    const response = (await api('post', 'predict', {data})) as TResponse;
    if (!response.success) {
      setState({...state, isLoading: false, error: {open: true, message: response.error!}});
      return;
    }
    setState({...state, isLoading: false, activeStep: 1}) //TODO add variables for predict result
  };

  useEffect(() => {
    reloadCatalogs(state.car.mark);
  }, [state.car.mark]);

  return (
    <Grid container className={classes.root}>
      <Grid container item xs={10} direction="column" className={classes.content}>
        <Stack spacing={5}>
          <Grid item container className={classes.logo}>
            <Avatar src="logo.png" alt="Auto Price" sx={{width: 40, height: 40}}/>
            <Typography variant="h4" textAlign="center">auto-price</Typography>
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
                {formGenerator(carFormInit, state.car, handleChange)}
                <Button variant="contained" type="submit">Оценить</Button>
              </Grid>
            ) : (
              <div>Predict Result Here</div>
            )}
          </Grid>
        </Stack>
      </Grid>
      <Backdrop open={state.isLoading}>
        <CircularProgress sx={{color: "#23D5ABFF"}}/>
      </Backdrop>
      {/*<Snackbar open={state.error.open} autoHideDuration={4000} onClose={handleCloseNotification} message={state.error.message}/>*/}
      {/*  <Alert variant="filled" severity="error">{state.error.message}</Alert>*/}
      {/*</Snackbar>*/}
    </Grid>
  );
}

export default Predict;
