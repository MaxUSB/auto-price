import './start.css';
import React from 'react';
import {DirectionsCar} from '@mui/icons-material'
import {Button, Grid, Typography} from '@mui/material'

const Start = () => {
  return (
    <Grid container className="root">
      <Grid container item xs={6} direction="column" className="content">
        <Typography variant="h3" textAlign="center">Добро пожаловать!</Typography>
        <Typography variant="h5" textAlign="center">Здесь вы можете узнать рекомендуемую рыночную стоимость вашего автомобиля.</Typography>
        <Button href="/predict" variant="contained" endIcon={<DirectionsCar/>}>Хочу попробовать</Button>
      </Grid>
    </Grid>
  );
}

export default Start;
