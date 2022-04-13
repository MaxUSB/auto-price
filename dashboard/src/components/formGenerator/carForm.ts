import {IFormItem, ISelectOption} from '.';

let marksOptions: ISelectOption[] = [];
let citiesOptions: ISelectOption[] = [];
let horsepowerOptions: ISelectOption[] = [];

const ptsOptions: ISelectOption[] = [
  {label: 'Оригинал', value: 'ORIGINAL'},
  {label: 'Дубликат', value: 'DUPLICATE'},
];
const fuelTypeOptions: ISelectOption[] = [
  {label: 'Бензин', value: 'GASOLINE'},
  {label: 'Дизель', value: 'DIESEL'},
];
const gearTypeOptions: ISelectOption[] = [
  {label: 'Передний', value: 'FORWARD_CONTROL'},
  {label: 'Задний', value: 'REAR_DRIVE'},
  {label: 'Полный', value: 'ALL_WHEEL_DRIVE'},
];
const transmissionOptions: ISelectOption[] = [
  {label: 'Механика', value: 'MECHANICAL'},
  {label: 'Автомат', value: 'AUTOMATIC'},
  {label: 'Робот', value: 'ROBOT'},
  {label: 'Вариатор', value: 'VARIATOR'},
];

const carForm = (cities: string[], marks: string[], horsepower: string[]): IFormItem[] => {
  citiesOptions = cities.map(city => ({label: city, value: city}));
  marksOptions = marks.map(mark => ({label: mark, value: mark}));
  horsepowerOptions = horsepower.map(horsepower => ({label: horsepower, value: horsepower}));

  return ([
    {
      field: 'city',
      elementType: 'autocomplete',
      label: 'Город',
      selectOptions: citiesOptions,
      groupBy: true,
    }, {
      field: 'mark',
      elementType: 'autocomplete',
      label: 'Марка',
      selectOptions: marksOptions,
      groupBy: true,
    }, {
      field: 'horsepower',
      elementType: 'autocomplete',
      label: 'Л.С.',
      selectOptions: horsepowerOptions,
    }, {
      field: 'year',
      elementType: 'text',
      label: 'Год выпуска',
    }, {
      field: 'mileage',
      elementType: 'text',
      label: 'Пробег',
    }, {
      field: 'owners',
      elementType: 'text',
      label: 'Кол-во владельцев',
    }, {
      field: 'pts',
      elementType: 'select',
      label: 'ПТС',
      selectOptions: ptsOptions,
    }, {
      field: 'fuelType',
      elementType: 'select',
      label: 'Тип топлива',
      selectOptions: fuelTypeOptions,
    }, {
      field: 'gearType',
      elementType: 'select',
      label: 'Привод',
      selectOptions: gearTypeOptions,
    }, {
      field: 'transmission',
      elementType: 'select',
      label: 'Тип КПП',
      selectOptions: transmissionOptions,
    },
  ]);
};

export default carForm;
