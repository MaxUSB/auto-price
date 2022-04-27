import React from "react";
import {createStyles, makeStyles} from '@mui/styles';
import {Grid, Stack, Typography} from '@mui/material';
import CurrencyRuble from '@mui/icons-material/CurrencyRuble';

const useStyles = makeStyles(() =>
  createStyles({
    root: {
      display: 'flex',
      justifyContent: "center",
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
  }),
);

interface IPredictResultsProps {
  predictedPrice: number | null;
  predictedError: number | null;
  mark?: string;
  model?: string;
}

const PredictResults = (props: IPredictResultsProps) => {
  const {predictedPrice, predictedError, mark, model} = props;
  const classes = useStyles();
  let markLinkPart = mark ? mark.toLowerCase().replace(' ', '-') : '';

  return (
    <Grid container className={classes.root}>
      {predictedPrice && predictedError ? (
        <Stack spacing={10}>
          <Grid item container className={classes.logo}>
            <img src={`//www.carlogos.org/car-logos/${markLinkPart}-logo.png`} alt="Логотип не найден" className={classes.logoImg}/>
            <Typography variant="h4" textAlign="center">{mark} {model}</Typography>
          </Grid>
          <Grid item container xs={12}>
            <Stack spacing={10}>
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
            </Stack>

          </Grid>
        </Stack>
      ) : null}
    </Grid>
  );
};

export default PredictResults;
