import {IFormItem, ISelectOption} from '.';

let marksOptions: ISelectOption[] = [];
let citiesOptions: ISelectOption[] = [];
let hpsOptions: ISelectOption[] = [];

const ptsOptions: ISelectOption[] = [{label: 'Оригинал', value: 'ORIGINAL'}, {label: 'Дубликат', value: 'DUPLICATE'}];

const carForm = (cities: string[], marks: string[], hps: number[]): IFormItem[] => {
  citiesOptions = cities.map(city => ({label: city, value: city}));
  marksOptions = marks.map(mark => ({label: mark, value: mark}));
  hpsOptions = hps.map(hp => ({label: hp, value: hp}));

  return ([
    {
      field: 'city',
      elementType: 'autocomplete',
      label: 'Город',
      selectOptions: citiesOptions,
    }, {
      field: 'mark',
      elementType: 'autocomplete',
      label: 'Марка',
      selectOptions: marksOptions,
    }, {
      field: 'hp',
      elementType: 'autocomplete',
      label: 'Л.С.',
      selectOptions: hpsOptions,
    }
    // {
    //   field: 'pts',
    //   elementType: 'select',
    //   label: 'ПТС',
    //   selectOptions: ptsOptions,
    // }, {
    //   field: 'mileage',
    //   elementType: 'text',
    //   label: 'Пробег',
    // }
  ]);
};

export default carForm;
