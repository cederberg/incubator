# findMatch — Iterative Refactoring

## 0. Original (`findBestMatch`, public)

```java
public Optional<CountryCode> findBestMatch(Mcc mcc, Mnc mnc) {
    String sql = """
        SELECT country_code, MIN(country_name) AS country_name
        FROM country_operator
        WHERE mcc = :mcc
          AND (mnc = :mnc OR :mnc IS NULL)
        GROUP BY country_code
        ORDER BY country_code ASC
        """;
    List<CountryCode> res =
        client.sql(sql)
        .param("mcc", Mapper.mapNullable(mcc, Mcc::getValue))
        .param("mnc", Mapper.mapNullable(mnc, Mnc::getValue))
        .query((rs, rowNum) -> new CountryCode(rs.getString("country_code"), rs.getString("country_name")))
        .list();
    return Optional.of(res)
        .filter(l -> l.size() == 1 || (l.size() > 1 && mnc != null))
        .map(l -> l.get(0));
}
```

## 1. Single SQL query, Java selection (first rewrite)

```java
private Optional<CountryOperator> findBestMatch(Mcc mcc, Mnc mnc) {
    if (mcc == null) return Optional.empty();
    String sql = "SELECT * FROM country_operator WHERE mcc = :mcc";
    List<CountryOperator> all = client.sql(sql)
        .param("mcc", mcc.getValue())
        .query(this::toOperator)
        .list();
    List<CountryOperator> exact = all.stream()
        .filter(op -> op.mnc().equals(mnc))
        .collect(toList());
    long distinct = all.stream().map(CountryOperator::country).distinct().count();
    if (!exact.isEmpty()) return Optional.of(exact.get(0));
    if (distinct == 1) return Optional.of(all.get(0));
    return Optional.empty();
}
```

## 2. Remove null guard, use `Mapper.mapNullable`, rename `distinct`

```java
private Optional<CountryOperator> findBestMatch(Mcc mcc, Mnc mnc) {
    String sql = "SELECT * FROM country_operator WHERE mcc = :mcc";
    List<CountryOperator> all = client.sql(sql)
        .param("mcc", Mapper.mapNullable(mcc, Mcc::getValue))
        .query(this::toOperator)
        .list();
    long countries = all.stream().map(CountryOperator::country).distinct().count();
    List<CountryOperator> exact = all.stream()
        .filter(op -> mnc != null && mnc.equals(op.mnc()))
        .collect(toList());
    if (!exact.isEmpty()) return Optional.of(exact.get(0));
    if (countries == 1) return Optional.of(all.get(0));
    return Optional.empty();
}
```

## 3. Replace list + get(0) with `findFirst().or()`

```java
private Optional<CountryOperator> findBestMatch(Mcc mcc, Mnc mnc) {
    String sql = "SELECT * FROM country_operator WHERE mcc = :mcc";
    List<CountryOperator> all = client.sql(sql)
        .param("mcc", Mapper.mapNullable(mcc, Mcc::getValue))
        .query(this::toOperator)
        .list();
    long countries = all.stream().map(CountryOperator::country).distinct().count();
    return all.stream()
        .filter(op -> mnc != null && mnc.equals(op.mnc()))
        .findFirst()
        .or(() -> countries == 1 ? all.stream().findFirst() : Optional.empty());
}
```

## 4. Constant predicate eliminates ternary

```java
private Optional<CountryOperator> findBestMatch(Mcc mcc, Mnc mnc) {
    String sql = "SELECT * FROM country_operator WHERE mcc = :mcc";
    List<CountryOperator> all = client.sql(sql)
        .param("mcc", Mapper.mapNullable(mcc, Mcc::getValue))
        .query(this::toOperator)
        .list();
    long countries = all.stream().map(CountryOperator::country).distinct().count();
    return all.stream()
        .filter(op -> mnc != null && mnc.equals(op.mnc()))
        .findFirst()
        .or(() -> all.stream().filter(op -> countries == 1).findFirst());
}
```

## 5. Combine predicates, drop `.or()`

```java
private Optional<CountryOperator> findBestMatch(Mcc mcc, Mnc mnc) {
    String sql = "SELECT * FROM country_operator WHERE mcc = :mcc";
    List<CountryOperator> all = client.sql(sql)
        .param("mcc", Mapper.mapNullable(mcc, Mcc::getValue))
        .query(this::toOperator)
        .list();
    long countries = all.stream().map(CountryOperator::country).distinct().count();
    return all.stream()
        .filter(op -> countries == 1 || (mnc != null && mnc.equals(op.mnc())))
        .findFirst();
}
```

## 6. `Objects.equals` handles null-MNC exact match; rename to `findMatch`

```java
private Optional<CountryOperator> findMatch(Mcc mcc, Mnc mnc) {
    String sql = "SELECT * FROM country_operator WHERE mcc = :mcc";
    List<CountryOperator> all = client.sql(sql)
        .param("mcc", Mapper.mapNullable(mcc, Mcc::getValue))
        .query(this::toOperator)
        .list();
    long countries = all.stream().map(CountryOperator::country).distinct().count();
    return all.stream()
        .filter(op -> countries == 1 || Objects.equals(mnc, op.mnc()))
        .findFirst();
}
```
