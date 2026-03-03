package com.vetpro.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.time.LocalDateTime;

@Entity
@Table(name = "hospitalizations")
public class Hospitalization {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @ManyToOne
    @JoinColumn(name = "pet_id", nullable = false)
    private Pet pet;

    @NotNull
    @ManyToOne
    @JoinColumn(name = "veterinarian_id", nullable = false)
    private User veterinarian;

    @NotNull
    @Column(nullable = false)
    private LocalDateTime admissionDate;

    private LocalDateTime dischargeDate;

    @NotBlank
    @Column(nullable = false)
    private String reason;

    private String status;

    private String dailyNotes;

    public Hospitalization() {
    }

    public Hospitalization(Pet pet, User veterinarian, LocalDateTime admissionDate, LocalDateTime dischargeDate, String reason, String status, String dailyNotes) {
        this.pet = pet;
        this.veterinarian = veterinarian;
        this.admissionDate = admissionDate;
        this.dischargeDate = dischargeDate;
        this.reason = reason;
        this.status = status;
        this.dailyNotes = dailyNotes;
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

    public User getVeterinarian() {
        return veterinarian;
    }

    public void setVeterinarian(User veterinarian) {
        this.veterinarian = veterinarian;
    }

    public LocalDateTime getAdmissionDate() {
        return admissionDate;
    }

    public void setAdmissionDate(LocalDateTime admissionDate) {
        this.admissionDate = admissionDate;
    }

    public LocalDateTime getDischargeDate() {
        return dischargeDate;
    }

    public void setDischargeDate(LocalDateTime dischargeDate) {
        this.dischargeDate = dischargeDate;
    }

    public String getReason() {
        return reason;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getDailyNotes() {
        return dailyNotes;
    }

    public void setDailyNotes(String dailyNotes) {
        this.dailyNotes = dailyNotes;
    }
}
