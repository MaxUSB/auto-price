import React from 'react';
import { DirectionsCar } from '@mui/icons-material'
import { createStyles, makeStyles } from '@mui/styles'
import { Button, Grid, Typography, Avatar } from '@mui/material'

const useStyles = makeStyles(() =>
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
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: '#FFFFFFB2',
    },
    logo: {
      gap: '20px',
      justifyContent: 'center',
    },
  }),
);

const Start = () => {
  const classes = useStyles();

  return (
    <Grid container className={classes.root}>
      <Grid container item xs={6} direction="column" className={classes.content}>
        <Grid item container className={classes.logo}>
          <Avatar src="logo.png" alt="Auto Price" sx={{ width: 40, height: 40 }}/>
          <Typography variant="h4" textAlign="center">auto-price</Typography>
        </Grid>
        <Typography variant="h5" textAlign="center">Здесь вы можете узнать рекомендуемую рыночную стоимость вашего автомобиля.</Typography>
        <Button href="/predict" variant="contained" endIcon={<DirectionsCar/>}>Хочу попробовать</Button>
      </Grid>
    </Grid>
  );
}

export default Start;
