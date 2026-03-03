package com.vetpro.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotNull;

import java.time.LocalDate;

@Entity
@Table(name = "vaccine_records")
public class VaccineRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @ManyToOne
    @JoinColumn(name = "pet_id", nullable = false)
    private Pet pet;

    @NotNull
    @ManyToOne
    @JoinColumn(name = "vaccine_id", nullable = false)
    private Vaccine vaccine;

    @NotNull
    @ManyToOne
    @JoinColumn(name = "administered_by_id", nullable = false)
    private User administeredBy;

    @NotNull
    @Column(nullable = false)
    private LocalDate dateAdministered;

    private LocalDate nextDueDate;

    private String batchNumber;

    public VaccineRecord() {
    }

    public VaccineRecord(Pet pet, Vaccine vaccine, User administeredBy, LocalDate dateAdministered, LocalDate nextDueDate, String batchNumber) {
        this.pet = pet;
        this.vaccine = vaccine;
        this.administeredBy = administeredBy;
        this.dateAdministered = dateAdministered;
        this.nextDueDate = nextDueDate;
        this.batchNumber = batchNumber;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Pet getPet() {
        return pet;
    }

    public void setPet(Pet pet) {
        this.pet = pet;
    }

    public Vaccine getVaccine() {
        return vaccine;
    }

    public void setVaccine(Vaccine vaccine) {
        this.vaccine = vaccine;
    }

    public User getAdministeredBy() {
        return administeredBy;
    }

    public void setAdministeredBy(User administeredBy) {
        this.administeredBy = administeredBy;
    }

    public LocalDate getDateAdministered() {
        return dateAdministered;
    }

    public void setDateAdministered(LocalDate dateAdministered) {
        this.dateAdministered = dateAdministered;
    }

    public LocalDate getNextDueDate() {
        return nextDueDate;
    }

    public void setNextDueDate(LocalDate nextDueDate) {
        this.nextDueDate = nextDueDate;
    }

    public String getBatchNumber() {
        return batchNumber;
    }

    public void setBatchNumber(String batchNumber) {
        this.batchNumber = batchNumber;
    }
}
