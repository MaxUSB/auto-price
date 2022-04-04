import React from 'react';
import {DirectionsCar} from '@mui/icons-material'
import {createStyles, makeStyles} from '@mui/styles'
import {Button, Grid, Theme, Typography} from '@mui/material'

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      height: '100vh',
      alignItems: 'center',
      justifyContent: 'center',
    },
    content: {
      gap: '40px',
      padding: '30px',
      borderRadius: '10px',
      justifyContent: 'center',
      backgroundColor: 'rgba(255, 255, 255, 0.7)',
    },
  }),
);

const Start = () => {
  const classes = useStyles();

  return (
    <Grid container className={classes.root}>
      <Grid container item xs={6} direction="column" className={classes.content}>
        <Typography variant="h3" textAlign="center">Добро пожаловать!</Typography>
        <Typography variant="h5" textAlign="center">Здесь вы можете узнать рекомендуемую рыночную стоимость вашего автомобиля.</Typography>
        <Button href="/predict" variant="contained" endIcon={<DirectionsCar/>}>Хочу попробовать</Button>
      </Grid>
    </Grid>
  );
}

export default Start;
