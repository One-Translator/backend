package com.example.spring_backend.entity;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import lombok.AccessLevel;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import jakarta.persistence.Id;
import org.springframework.data.annotation.CreatedDate;

@Entity
@Getter
@Builder
@AllArgsConstructor(access = AccessLevel.PROTECTED)
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class ValidDataset {

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(columnDefinition = "text")
  private String resultData;

  @Column(columnDefinition = "text")
  private String originalData;

  @Column(columnDefinition = "varchar(2048)")
  private String originalDomain;

  @Column(columnDefinition = "varchar(2048)")
  private String originalUrl;

  private Integer level;

  @CreatedDate
  @Column(updatable = false)
  private LocalDateTime createdAt;
}
