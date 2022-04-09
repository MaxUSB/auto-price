import React from "react";
import {createStyles, makeStyles} from '@mui/styles';
import CurrencyRuble from '@mui/icons-material/CurrencyRuble';
import {Grid, Avatar, Stack, Typography} from "@mui/material";

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
  }),
);

interface IPredictResultsProps {
  predictedPrice: number | null;
  predictedError: number | null;
  mark?: string;
  markLogo: string | null;
}

const PredictResults = (props: IPredictResultsProps) => {
  const {predictedPrice, predictedError, mark, markLogo} = props;
  const classes = useStyles();
  let downRangeLimit = 0;
  let upRangeLimit = 0;

  if (predictedPrice && predictedError) {
    downRangeLimit = predictedPrice - predictedPrice * predictedError;
    upRangeLimit = predictedPrice + predictedPrice * predictedError;
  }

  return (
    <Grid container className={classes.root}>
      {predictedPrice && predictedError ? (
        <Stack spacing={10}>
          <Grid item container className={classes.logo}>
            <Avatar src={markLogo ? markLogo : ''} alt="Mark Logo" sx={{width: 100, height: 100}}/>
            <Typography variant="h4" textAlign="center">{mark}</Typography>
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
                  {`${downRangeLimit.toLocaleString('ru-RU')} - ${upRangeLimit.toLocaleString('ru-RU')}`}
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
