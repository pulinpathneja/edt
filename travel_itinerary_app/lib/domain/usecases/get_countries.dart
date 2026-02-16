import '../entities/country.dart';
import '../repositories/country_repository.dart';

class GetCountries {
  final CountryRepository repository;

  GetCountries(this.repository);

  Future<List<Country>> call() {
    return repository.getCountries();
  }
}
