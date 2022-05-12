import 'chart.js/auto';
import React from "react";
import LineChart from './LineChart';
import { createStyles, makeStyles } from '@mui/styles';
import { Grid, Stack, Typography } from '@mui/material';
import { CurrencyRuble } from '@mui/icons-material';

const useStyles = makeStyles(() =>
  createStyles({
    root: {
      display: 'flex',
    },
    logo: {
      gap: '20px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    },
    logoImg: {
      maxHeight: '100px',
    },
    fullWidth: {
      width: '100%',
      justifyContent: 'center',
      alignItems: 'center',
    },
  }),
);

interface IPredictResultsProps {
  predictedPrice: number | null;
  predictedError: number | null;
  similarCars: any[];
  mark?: string;
  model?: string;
}

const PredictResults = (props: IPredictResultsProps) => {
  const { predictedPrice, predictedError, similarCars, mark, model } = props;
  const classes = useStyles();
  const markLinkPart = mark ? mark.toLowerCase().replace(' ', '-') : '';

  return (
    <Grid container className={classes.root}>
      {predictedPrice && predictedError ? (
        <Stack spacing={10} className={classes.fullWidth}>
          <Grid item container className={classes.logo}>
            <img src={`//www.carlogos.org/car-logos/${markLinkPart}-logo.png`} alt="Логотип не найден" className={classes.logoImg}/>
            <Typography variant="h4" textAlign="center">{mark} {model}</Typography>
          </Grid>
          <Grid item container xs={12} className={classes.fullWidth}>
            <Stack spacing={10} className={classes.fullWidth}>
              <Stack spacing={2}>
                <Typography variant="h3" textAlign="center">
                  {predictedPrice.toLocaleString('ru-RU')}
                  <CurrencyRuble fontSize="large"/>
                </Typography>
                <Typography variant="h5" textAlign="center">рекомендуемая стоимость по вашим параметрам</Typography>
              </Stack>
              <Stack spacing={2}>
                <Typography variant="h3" textAlign="center">
                  {`${(predictedPrice - predictedError).toLocaleString('ru-RU')} - ${(predictedPrice + predictedError).toLocaleString('ru-RU')}`}
                  <CurrencyRuble fontSize="large"/>
                </Typography>
                <Typography variant="h5" textAlign="center">возможный диапозон стоимости</Typography>
              </Stack>
              {similarCars ? (
                <Stack spacing={2} className={classes.fullWidth}>
                  <Typography variant="h5" textAlign="center">График стоимостей похожих авто:</Typography>
                  <LineChart data={similarCars}/>
                </Stack>
              ) : null}
            </Stack>
          </Grid>
        </Stack>
      ) : null}
    </Grid>
  );
};

export default PredictResults;
