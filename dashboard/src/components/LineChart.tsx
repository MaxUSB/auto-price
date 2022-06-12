import React from 'react';
import { ChartData } from 'chart.js';
import { Chart } from 'react-chartjs-2';
import { createStyles, makeStyles } from '@mui/styles';

const useStyles = makeStyles(() =>
  createStyles({
    root: {
      width: '80%',
    },
  }),
);

interface ILineChartProps {
  data: any[];
}

const LineChart = (props: ILineChartProps) => {
  const { data } = props;
  const classes = useStyles();

  const getChartData = (similarCars: any[]): ChartData => ({
    labels: similarCars ? similarCars.map((car, index) => `Авто ${index + 1}`) : [],
    datasets: similarCars ? [{
      label: 'Стоимость',
      data: similarCars.map(car => car['Price']),
      fill: true,
      borderColor: 'rgba(35, 213, 171, 1)',
      backgroundColor: 'rgba(35, 213, 171, 0.7)',
    }] : [],
  });

  return (
    <div className={classes.root}>
      <Chart
        type="bar"
        data={getChartData(data)}
        options={{
          hover: {
            intersect: false,
            mode: 'index'
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              intersect: false,
              mode: 'index',
              displayColors: false,
              callbacks: {
                title: (context) => {
                  const car = data[context[0]['dataIndex']];
                  return `${car['Mark']} ${car['Model']}, ${car['Year']}`;
                },
                label: (context) => {
                  const car = data[context['dataIndex']];
                  return `Л.С.: ${car['Horsepower']}; Пробег: ${car['Mileage'].toLocaleString('ru-RU')} км; Владельцы: ${car['Owners']}; Клиренс: ${car['Clearance']}`;
                },
                footer: (context) => {
                  const car = data[context[0]['dataIndex']];
                  return `Стоимость: ${car['Price'].toLocaleString('ru-RU')} ₽`;
                },
              },
            },
          },
        }}
      />
    </div>
  );
};

export default LineChart;
