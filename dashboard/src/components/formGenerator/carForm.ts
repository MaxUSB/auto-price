import { IFormItem, ISelectOption } from '.';

let marksOptions: ISelectOption[] = [];
let modelsOptions: ISelectOption[] = [];
let citiesOptions: ISelectOption[] = [];
let horsepowerOptions: ISelectOption[] = [];
let clearancesOptions: ISelectOption[] = [];

const carForm = (cities: string[], marks: string[], models: string[], horsepower: string[], clearance: string[]): IFormItem[] => {
  citiesOptions = cities.map(city => ({ label: city, value: city }));
  marksOptions = marks.map(mark => ({ label: mark, value: mark }));
  modelsOptions = models.map(model => ({ label: model, value: model }));
  horsepowerOptions = horsepower.map(horsepower => ({ label: horsepower, value: horsepower }));
  clearancesOptions = clearance.map(clearance => ({ label: clearance, value: clearance }));

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
      field: 'model',
      elementType: 'autocomplete',
      label: 'Модель',
      selectOptions: modelsOptions,
      groupBy: true,
    }, {
      field: 'horsepower',
      elementType: 'autocomplete',
      label: 'Л.С.',
      selectOptions: horsepowerOptions,
    }, {
      field: 'clearance',
      elementType: 'autocomplete',
      label: 'Клиренс',
      selectOptions: clearancesOptions,
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
    },
  ]);
};

export default carForm;
