package com.example.spring_backend.repository;

import com.example.spring_backend.entity.ValidDataset;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ValidDatasetRepository extends JpaRepository<ValidDataset, Long> {

}
